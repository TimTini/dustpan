"""Native Fusion reconstruction. Numeric section profiles use the declared rebuild route."""
from pathlib import Path
import importlib.util
import json
import hashlib
import traceback

_spec=importlib.util.spec_from_file_location('dustpan_geometry',Path(__file__).with_name('geometry.py'))
_geo=importlib.util.module_from_spec(_spec);_spec.loader.exec_module(_geo)
DEFAULTS=_geo.DEFAULTS
SOURCE_SHA256=_geo.SOURCE_SHA256
REINFORCE_FLOOR=True
REINFORCE_HANDLE=True
REINFORCE_WALLS=True
REINFORCE_RIM=True
for _name in ['resolve_parameters','layout','floor_sections','sample_path','outer_path','rim_sections','floor_lift','rib_path','rim_z']:
    globals()[_name]=getattr(_geo,_name)

class Builder:
    def __init__(self,design,parameters,flags,progress=print):
        import adsk.core as core
        import adsk.fusion as fusion
        self.core=core;self.fusion=fusion;self.design=design;self.comp=design.rootComponent
        self.p=parameters;self.flags=flags;self.g=layout(parameters,flags);self.progress=progress
        self.new=fusion.FeatureOperations.NewBodyFeatureOperation
        self.stage='parameters'
        for name,number in parameters.items():
            expression='0.1 * depth' if name=='floor_start' and abs(number-0.1*parameters['depth'])<1e-9 else str(number)+' mm'
            if name=='ramp_angle':expression=str(number)+' deg'
            units='deg' if name=='ramp_angle' else 'mm'
            design.userParameters.add(name,core.ValueInput.createByString(expression),units,
                _geo.COMMENTS[name]+'; rebuild section geometry with Run')
        for name,(expr,unit) in _geo.DERIVED.items():
            design.userParameters.add(name,core.ValueInput.createByString(expr),unit,'Derived formula')
        self.main=None
        self.planes={}

    def mark(self,name):
        self.stage=name;self.progress(name)

    def value(self,expr):return self.core.ValueInput.createByString(str(expr))

    def collection(self,items):
        c=self.core.ObjectCollection.create()
        for item in items:c.add(item)
        return c

    def plane(self,axis,position):
        key=(axis,round(position,9))
        if key in self.planes:return self.planes[key]
        base={'z':self.comp.xYConstructionPlane,'y':self.comp.xZConstructionPlane,'x':self.comp.yZConstructionPlane}[axis]
        inp=self.comp.constructionPlanes.createInput()
        # Offset follows the actual datum normal for this Fusion build.
        normal_component=getattr(base.geometry.normal,axis)
        if abs(normal_component)<0.99:raise RuntimeError('Unexpected datum normal for '+axis)
        offset=position/normal_component
        inp.setByOffset(base,self.value(str(offset)+' mm'))
        plane=self.comp.constructionPlanes.add(inp);plane.name=axis+'='+str(position)+' mm';plane.isLightBulbOn=False
        self.planes[key]=plane
        return plane

    def profile(self,name,axis,position,path,mirror=1,inset=False):
        self.mark(name)
        sketch=self.comp.sketches.add(self.plane(axis,position));sketch.name=name
        sketch.isComputeDeferred=True
        def point(xy):
            a,b=xy
            xyz=(mirror*a,b,position) if axis=='z' else (mirror*a,position,b) if axis=='y' else (position,a,b)
            world=self.core.Point3D.create(*(v/10 for v in xyz))
            local=sketch.modelToSketchSpace(world)
            back=sketch.sketchToModelSpace(local)
            if abs(local.z)>1e-7 or back.distanceTo(world)>1e-7:raise RuntimeError(name+': profile point must lie on sketch plane')
            return local
        first=None;last=None
        def connect(p):
            nonlocal first,last
            if first is None:first=p
            if last is not None and last.distanceTo(p)>1e-7:
                curve=sketch.sketchCurves.sketchLines.addByTwoPoints(last,p);curve.isFixed=True
            last=p
        try:
            for s in path:
                if s[0]=='point':connect(point(s[1]));continue
                _,c,r,a,b=s
                if r<=0:raise ValueError(name+': positive arc radius required')
                import math
                def at(angle):return point((c[0]+r*math.cos(math.radians(angle)),c[1]+r*math.sin(math.radians(angle))))
                start=at(a);middle=at((a+b)/2);end=at(b)
                connect(start)
                curve=sketch.sketchCurves.sketchArcs.addByThreePoints(start,middle,end);curve.isFixed=True
                last=end
            connect(first)
        finally:sketch.isComputeDeferred=False
        if inset:
            curves=[sketch.sketchCurves.item(i) for i in range(sketch.sketchCurves.count)]
            inp=sketch.geometricConstraints.createOffsetInput(curves,self.value('-thickness / 2'))
            offset=sketch.geometricConstraints.addOffset2(inp)
            for curve in curves:curve.isConstruction=True
            for curve in offset.childCurves:curve.isConstruction=False
        if sketch.profiles.count!=1:raise RuntimeError(name+': expected one profile; got '+str(sketch.profiles.count))
        sketch.isVisible=False
        return sketch.profiles.item(0)

    def extrude(self,profile,distance,name,direction=None,symmetric=False):
        self.mark(name)
        inp=self.comp.features.extrudeFeatures.createInput(profile,self.new)
        if symmetric:inp.setSymmetricExtent(self.value(distance),True)
        else:
            sk=profile.parentSketch
            origin=sk.sketchToModelSpace(self.core.Point3D.create(0,0,0))
            normal=origin.vectorTo(sk.sketchToModelSpace(self.core.Point3D.create(0,0,1)))
            components=[normal.x,normal.y,normal.z];axis=max(range(3),key=lambda i:abs(components[i]))
            extent_direction=self.fusion.ExtentDirections.PositiveExtentDirection if components[axis]>0 else self.fusion.ExtentDirections.NegativeExtentDirection
            inp.setOneSideExtent(self.fusion.DistanceExtentDefinition.create(self.value(distance)),extent_direction if direction is None else direction)
        feat=self.comp.features.extrudeFeatures.add(inp);feat.name=name
        return feat.bodies.item(0)

    def loft(self,profiles,name):
        self.mark(name)
        inp=self.comp.features.loftFeatures.createInput(self.new);inp.isSolid=True
        for profile in profiles:inp.loftSections.add(profile)
        feature=self.comp.features.loftFeatures.add(inp);feature.name=name
        return feature.bodies.item(0)

    def combine(self,target,tool,operation,name):
        self.mark(name)
        inp=self.comp.features.combineFeatures.createInput(target,self.collection([tool]))
        inp.operation=getattr(self.fusion.FeatureOperations,operation+'FeatureOperation');inp.isKeepToolBodies=False
        feature=self.comp.features.combineFeatures.add(inp);feature.name=name
        if feature.bodies.count!=1:raise RuntimeError(name+': expected one result body')
        return feature.bodies.item(0)

    def cavity(self,lift,tag):
        sections=_geo.cavity_sections(self.p,lift)
        profiles=[self.profile(tag+' section '+str(i),'z',z,path) for i,(z,path) in enumerate(sections)]
        tool=self.loft(profiles,tag+' rounded cove loft')
        upper=self.extrude(profiles[-1],str(self.p['total_height']+10)+' mm',tag+' upper cavity')
        return self.combine(tool,upper,'Join',tag+' tool join')

    def envelope(self,name,span=None):
        pr=self.profile(name+' profile','x',0,_geo.envelope_path(self.p))
        return self.extrude(pr,str(span if span is not None else self.p['width']+2)+' mm',name,symmetric=True)

    def rectangle(self,name,axis,position,x0,y0,x1,y1):
        return self.profile(name,axis,position,[('point',q) for q in [(x0,y0),(x1,y0),(x1,y1),(x0,y1)]])

    def join(self,tool,name):self.main=self.combine(self.main,tool,'Join',name)

    def build(self):
        p=self.p;g=self.g
        pr=self.profile('Outer footprint','z',0,_geo.outer_path(p))
        self.main=self.extrude(pr,'wall_height','Outer blank')
        self.main=self.combine(self.main,self.envelope('Front ramp envelope'),'Intersect','Trim front ramp')
        self.main=self.combine(self.main,self.cavity(0,'Original cavity'),'Cut','Cut rounded cavity')
        if self.flags['rim']:
            for side in [-1,1]:
                profiles=[self.profile('Rim side '+str(side)+' section '+str(i),'y',y,path,side) for i,(y,path) in enumerate(_geo.rim_sections(p))]
                # Match the source's piecewise sections; a single global Loft can
                # interpolate across the taper/arc/flat transitions incorrectly.
                rim=self.loft(profiles[:2],'Rim segment '+str(side)+' 0')
                for i in range(1,len(profiles)-1):
                    piece=self.loft(profiles[i:i+2],'Rim segment '+str(side)+' '+str(i))
                    rim=self.combine(rim,piece,'Join','Join adjacent rim sections')
                self.join(rim,'Join side rim '+str(side))
                # Revolve a triangular section around the corner's vertical axis.
                if side==1:axis='y';position=g['cy'];center=g['cx']
                else:axis='x';position=-g['cx'];center=g['cy']
                path=[('point',q) for q in [(center+p['rear_radius']-.5,p['wall_height']-p['rim_height']),
                    (center+p['rear_radius']+p['rim_projection'],p['wall_height']),
                    (center+p['rear_radius']-.5,p['wall_height'])]]
                pr=self.profile('Corner rim '+str(side),axis,position,path)
                sk=pr.parentSketch
                def local(z):
                    xyz=(center,position,z) if axis=='y' else (position,center,z)
                    return sk.modelToSketchSpace(self.core.Point3D.create(*(v/10 for v in xyz)))
                ax=sk.sketchCurves.sketchLines.addByTwoPoints(local(0),local(p['wall_height']));ax.isConstruction=True;ax.isFixed=True
                pr=sk.profiles.item(0)  # Reacquire after the construction-axis edit.
                inp=self.comp.features.revolveFeatures.createInput(pr,ax,self.new)
                inp.setAngleExtent(False,self.value('90 deg' if side==1 else '-90 deg'))
                feat=self.comp.features.revolveFeatures.add(inp);feat.name='Corner rim revolve '+str(side)
                box=feat.bodies.item(0).preciseBoundingBox
                expected_x=(g['cx'],g['half']+p['rim_projection']) if side==1 else (-g['half']-p['rim_projection'],-g['cx'])
                if abs(box.minPoint.x*10-expected_x[0])>.01 or abs(box.maxPoint.x*10-expected_x[1])>.01:raise RuntimeError('Corner revolve quadrant mismatch')
                self.join(feat.bodies.item(0),'Join corner rim '+str(side))
            path=[('point',q) for q in [(g['back']-.5,p['wall_height']-p['rim_height']),
                (g['back']+p['rim_projection'],p['wall_height']),(g['back']-.5,p['wall_height'])]]
            pr=self.profile('Rear rim triangle','x',0,path)
            self.join(self.extrude(pr,str(2*g['cx'])+' mm','Rear rim extrusion',symmetric=True),'Join rear rim')
        if self.flags['floor']:
            profiles=[self.profile('Floor S section '+str(i),'y',y,path) for i,(y,path) in enumerate(_geo.floor_sections(p))]
            self.join(self.loft(profiles,'Floor S transition with side coves'),'Join floor transition')
            pad=self.extrude(self.profile('Rear pad footprint','z',0,_geo.outer_path(p),inset=True),str(_geo.pad_cap(p))+' mm','Rear pad blank')
            pad=self.combine(pad,self.cavity(p['floor_rear_extra'],'Raised rear cavity'),'Cut','Cut raised rear cove')
            pr=self.rectangle('Rear pad clipping','z',0,-g['half']-1,p['floor_start']+p['floor_ramp'],g['half']+1,g['back']+g['hr']+1)
            clip=self.extrude(pr,str(_geo.pad_cap(p))+' mm','Rear pad clipping tool')
            pad=self.combine(pad,clip,'Intersect','Clip rear pad')
            self.join(pad,'Join rear pad')
        if self.flags['handle']:
            for side in [-1,1]:
                x=side*g['hr']*.55-p['brace_thickness']/2
                path=[('point',q) for q in [(g['back']-.5,0),(g['back']+p['brace_reach'],0),
                    (g['hy']+g['hr']*.65,p['wall_height']+p['brace_rise']),
                    (g['back']-.5,p['wall_height']+p['brace_rise'])]]
                pr=self.profile('Handle brace '+str(side),'x',x,path)
                self.join(self.extrude(pr,'brace_thickness','Handle brace solid '+str(side)),'Join handle brace '+str(side))
        if self.flags['walls']:
            for side in [-1,1]:
                for y in [-p['depth']*.05,p['depth']*.25]:
                    pr=self.profile('Rounded wall rib '+str((side,y)),'y',y-p['wall_rib_width']/2,_geo.rib_path(p),side)
                    rib=self.extrude(pr,'wall_rib_width','Rounded rib extrusion')
                    box=rib.preciseBoundingBox
                    if abs(box.minPoint.y*10-(y-p['wall_rib_width']/2))>.01 or abs(box.maxPoint.y*10-(y+p['wall_rib_width']/2))>.01:raise RuntimeError('Rib Y placement mismatch')
                    rib=self.combine(rib,self.envelope('Rib height envelope',p['width']+2*p['wall_rib_projection']+2),'Intersect','Trim rounded rib')
                    self.join(rib,'Join rounded rib')
        # Circle and extrusion retain an actual expression for total_height.
        sk=self.comp.sketches.add(self.comp.xYConstructionPlane);sk.name='Handle circle'
        c=sk.sketchCurves.sketchCircles.addByCenterRadius(self.core.Point3D.create(0,g['hy']/10,0),g['hr']/10);c.isFixed=True
        sk.isVisible=False
        self.join(self.extrude(sk.profiles.item(0),'total_height','Handle extrusion'),'Join handle')
        self.main.name='Dustpan'
        self.design.attributes.add('dustpan','parameters',json.dumps(self.p))
        self.design.attributes.add('dustpan','flags',json.dumps(self.flags))
        return self.main

def build(design,reinforce=None,parameters=None,progress=print):
    flags=reinforce or dict(floor=REINFORCE_FLOOR,handle=REINFORCE_HANDLE,walls=REINFORCE_WALLS,rim=REINFORCE_RIM)
    builder=Builder(design,resolve_parameters(parameters),flags,progress)
    try:return builder.build()
    except Exception as exc:raise RuntimeError('Fusion stage '+builder.stage+': '+str(exc)) from exc

def check_model(design,reinforce=None,parameters=None):
    import adsk.fusion as fusion
    p=resolve_parameters(parameters);expected=layout(p,reinforce)
    if design.rootComponent.bRepBodies.count!=1:raise RuntimeError('Expected exactly one native body')
    body=design.rootComponent.bRepBodies.item(0)
    if not body.isSolid:raise RuntimeError('Expected a native solid')
    bad=[]
    for i in range(design.timeline.count):
        entity=design.timeline.item(i).entity
        if hasattr(entity,'healthState') and entity.healthState!=fusion.FeatureHealthStates.HealthyFeatureHealthState:
            bad.append((i,getattr(entity,'name',''),getattr(entity,'errorOrWarningMessage','')))
    if bad:raise RuntimeError('Unhealthy timeline: '+str(bad))
    box=body.preciseBoundingBox
    bounds=[[10*getattr(pt,axis) for axis in 'xyz'] for pt in [box.minPoint,box.maxPoint]]
    if any(abs(bounds[i][j]-expected['bounds_mm'][i][j])>.05 for i in range(2) for j in range(3)):
        raise RuntimeError('Bounds mismatch: '+str(bounds))
    return dict(bounds_mm=bounds,extents_mm=[bounds[1][i]-bounds[0][i] for i in range(3)],
        volume_mm3=body.volume*1000,bodies=1,timeline=design.timeline.count,health='passed')

def run(context):
    import adsk.core as core
    import adsk.fusion as fusion
    app=core.Application.get()
    try:
        parameters=None
        active=fusion.Design.cast(app.activeProduct)
        if active and active.attributes.itemByName('dustpan','parameters'):
            parameters={name:active.userParameters.itemByName(name).value*(180/3.141592653589793 if name=='ramp_angle' else 10) for name in DEFAULTS}
        doc=app.documents.add(core.DocumentTypes.FusionDesignDocumentType);doc.name='Dustpan corrected native'
        design=fusion.Design.cast(app.activeProduct);design.designType=fusion.DesignTypes.ParametricDesignType
        build(design,parameters=parameters);check_model(design,parameters=parameters)
        app.activeViewport.fit()
        app.userInterface.messageBox('Native build completed. Geometry fidelity is verified by the export audit. Run rebuilds section profiles using the current Dustpan user parameters.')
    except Exception:app.userInterface.messageBox(traceback.format_exc())
