"""Source-derived geometry in mm; consumed by the native Fusion builder."""

import math

ARC_STEPS = 48
FILLET_STEPS = 24

def resolve_parameters(overrides=None):
    p = dict(DEFAULTS)
    p.update(overrides or {})
    if not overrides or 'floor_start' not in overrides:
        p['floor_start'] = 0.1*p['depth']
    return p

def arc(center, radius, start, end):
    return ('arc', center, radius, start, end)

def line(point):
    return ('point', point)

def sample_path(path, steps=48):
    points = []
    for s in path:
        if s[0] == 'point':
            points.append(s[1])
        else:
            _, c, r, a, b = s
            points.extend((c[0]+r*math.cos(math.radians(a+(b-a)*i/steps)),
                           c[1]+r*math.sin(math.radians(a+(b-a)*i/steps)))
                          for i in range(steps+1))
    return points

def mirror_reverse(path):
    result=[]
    for s in reversed(path):
        if s[0]=='point':
            result.append(line((-s[1][0],s[1][1])))
        else:
            _,c,r,a,b=s
            result.append(arc((-c[0],c[1]),r,180-b,180-a))
    return result

def outer_path(p):
    g=layout(p,dict.fromkeys(['floor','handle','walls','rim'],False))
    right=[arc((g['cx'],g['cy']),p['rear_radius'],0,90),
           arc((g['jx'],g['back']+p['handle_fillet']),p['handle_fillet'],-90,g['outer_angle'])]
    return [line((g['half'],g['front']))]+right+[
        arc((0,g['hy']),g['hr'],g['ha'],180-g['ha'])]+mirror_reverse(right)+[
        line((-g['half'],g['front']))]

def cavity_path(p,inset):
    g=layout(p,dict.fromkeys(['floor','handle','walls','rim'],False))
    right=[arc((g['cx'],g['cy']),p['rear_radius']-p['thickness']-inset,0,90),
           arc((g['jx'],g['back']-p['thickness']-p['handle_fillet']),
               p['handle_fillet']-inset,90,g['inner_angle'])]
    return [line((g['half']-p['thickness']-inset,g['front']-10))]+right+[
        arc((0,g['hy']),g['hr']+inset+0.01,360-g['ha'],180+g['ha'])]+mirror_reverse(right)+[
        line((-g['half']+p['thickness']+inset,g['front']-10))]

def cavity_sections(p,lift=0):
    # Resolve the zero-radius blend at the bottom within0.01mm of source.
    result=[]
    for i in range(FILLET_STEPS+1):
        a=-89.9 if i==0 else -90+90*i/FILLET_STEPS
        d=p['floor_fillet']*(1-math.cos(math.radians(a)))
        z=p['thickness']+lift+p['floor_fillet']*(1+math.sin(math.radians(a)))
        if i==0:z=p['thickness']+lift
        result.append((z,cavity_path(p,d)))
    return result

def pad_cap(p):
    base=p['thickness']+p['floor_rear_extra']+p['floor_fillet']
    return base+min(0.5,(p['wall_height']-base)/2)

def floor_sections(p):
    ys=[p['floor_start']+p['floor_ramp']*i/FILLET_STEPS for i in range(FILLET_STEPS+1)]
    ys.append(ys[-1]+0.5)
    result=[]
    r=p['floor_fillet'];half=p['width']/2;t=p['thickness']
    for y in ys:
        z=t+r+floor_lift(y,p)
        result.append((y,[line((-half+t-0.2,t-0.5)),line((half-t+0.2,t-0.5)),
            line((half-t+0.2,z)),arc((half-t-r,z),r,0,-90),
            arc((-half+t+r,z),r,-90,-180),line((-half+t-0.2,z))]))
    return result

def rim_sections(p):
    y0=-p['depth']/2+p['rim_start'];cy=p['depth']/2-p['rear_radius'];half=p['width']/2
    result=[]
    for i in range(ARC_STEPS+1):
        y=y0+(cy-y0)*i/ARC_STEPS
        t=min(1,max(0,(y-y0)/p['rim_taper']));z=rim_z(y,p)
        result.append((y,[line((half-0.5,z-p['rim_height'])),
            line((half+p['rim_projection']*t,z)),line((half-0.5,z))]))
    return result

def rib_path(p):
    h=p['width']/2;r=p['wall_rib_radius']
    centers=[(h-0.5,r),(h+p['wall_rib_projection']-r,r),(h-0.5,p['wall_height']-r)]
    normals=[]
    for i,c in enumerate(centers):
        q=centers[(i+1)%3];normals.append(math.degrees(math.atan2(-(q[0]-c[0]),q[1]-c[1])))
    result=[]
    for i,c in enumerate(centers):
        a=normals[(i-1)%3];b=normals[i]
        while b<=a:b+=360
        result.append(arc(c,r,a,b))
    return result

def envelope_path(p):
    front=-p['depth']/2;top=p['wall_height'];r=p['ramp_radius']
    ry=front+(top+r*(1/math.cos(math.radians(p['ramp_angle']))-1))/math.tan(math.radians(p['ramp_angle']))
    far=p['depth']/2+p['handle_diameter']/2+20
    return [line((front,0)),line((far,0)),line((far,top)),
            arc((ry,top-r),r,90,90+p['ramp_angle'])]

REINFORCE_FLOOR = True

REINFORCE_HANDLE = True

REINFORCE_WALLS = True

REINFORCE_RIM = True

SOURCE_SHA256 = '9f8a284a37d630a114eb1b5773fc276a5a30d8fef1dacd14db03247d8cb54db2'

DEFAULTS = {
    'width': 200, 'depth': 200, 'wall_height': 50, 'thickness': 3,
    'rear_radius': 23, 'handle_diameter': 20, 'total_height': 250,
    'floor_rear_extra': 1.2, 'floor_start': 20, 'floor_ramp': 30,
    'brace_thickness': 3, 'brace_reach': 15, 'brace_rise': 15,
    'wall_rib_projection': 3, 'wall_rib_width': 4, 'wall_rib_radius': 1,
    'rim_projection': 3, 'rim_height': 6, 'rim_start': 20, 'rim_taper': 20,
    'floor_fillet': 5, 'handle_fillet': 5, 'ramp_angle': 30, 'ramp_radius': 100,
}

COMMENTS = {
    'width': 'Chiều ngang ngoài khay',
    'depth': 'Chiều sâu ngoài khay (trục Y)',
    'wall_height': 'Cao thành; đáy in tại Z0',
    'thickness': 'Dày thành và đáy danh nghĩa',
    'rear_radius': 'Bo góc sau ngoài',
    'handle_diameter': 'Đường kính cán',
    'total_height': 'Cao tổng gồm cán',
    'floor_rear_extra': 'Đắp thêm đáy sau khi reinforce_floor',
    'floor_start': 'Y bắt đầu chuyển tiếp đáy (từ tâm; SCAD 0.1*depth)',
    'floor_ramp': 'Chiều dài chuyển tiếp đáy',
    'brace_thickness': 'Dày gân cán',
    'brace_reach': 'Độ nhô gân cán ra sau mép sau',
    'brace_rise': 'Cao gân cán trên mép thành',
    'wall_rib_projection': 'Độ nhô gân thành bên',
    'wall_rib_width': 'Rộng gân thành bên',
    'wall_rib_radius': 'Bo tiết diện gân thành',
    'rim_projection': 'Độ nhô vành ngoài',
    'rim_height': 'Cao vành',
    'rim_start': 'Giữ mép hót trước khi thuôn vành',
    'rim_taper': 'Chiều dài thuôn vành',
    'floor_fillet': 'Bo đáy–thành lòng',
    'handle_fillet': 'Bo lõm nối thành–cán',
    'ramp_angle': 'Góc dốc mép hót',
    'ramp_radius': 'Bo tiếp tuyến mép hót–đỉnh thành',
}

DERIVED = {
    'half_width': ('width / 2', 'mm'),
    'y_front': ('-depth / 2', 'mm'),
    'y_back': ('depth / 2', 'mm'),
    'handle_radius': ('handle_diameter / 2', 'mm'),
    'handle_y': ('y_back - thickness / 2', 'mm'),
    'corner_cx': ('half_width - rear_radius', 'mm'),
    'corner_cy': ('y_back - rear_radius', 'mm'),
    'blend_jx': (
        'sqrt((handle_radius + handle_fillet) * (handle_radius + handle_fillet) - '
        '(handle_fillet + thickness / 2) * (handle_fillet + thickness / 2))', 'mm'),
}

def layout(p, reinforce=None):
    """Validate SCAD asserts and return expected bounds / key landmarks."""
    reinforce = reinforce or {
        'floor': REINFORCE_FLOOR, 'handle': REINFORCE_HANDLE,
        'walls': REINFORCE_WALLS, 'rim': REINFORCE_RIM,
    }

    def require(ok, message):
        if not ok:
            raise ValueError(message)

    require(all(math.isfinite(v) for v in p.values()), 'Tham số phải hữu hạn.')
    require(p['thickness'] > 0 and p['thickness'] < p['rear_radius'],
            'thickness phải trong (0, rear_radius).')
    require(p['handle_diameter'] > p['thickness'] and p['handle_fillet'] > 0,
            'handle_diameter > thickness; handle_fillet > 0.')
    require(p['rear_radius'] > p['thickness'] + p['floor_fillet'],
            'rear_radius phải lớn hơn thickness + floor_fillet.')
    require(0 < p['floor_fillet'] <= p['handle_fillet'],
            'floor_fillet phải trong (0, handle_fillet].')
    require(p['rear_radius'] < min(p['width'], p['depth']) / 2,
            'rear_radius phải nhỏ hơn nửa width và depth.')
    require(p['wall_height'] > p['thickness'] + p['floor_fillet'] and p['ramp_radius'] > 0,
            'wall_height / ramp_radius không hợp lệ.')
    require(p['total_height'] >= p['wall_height'] and 0 < p['ramp_angle'] < 90,
            'total_height / ramp_angle không hợp lệ.')

    half = p['width'] / 2
    front = -p['depth'] / 2
    back = p['depth'] / 2
    hr = p['handle_diameter'] / 2
    hy = back - p['thickness'] / 2
    cx = half - p['rear_radius']
    cy = back - p['rear_radius']
    jx = math.sqrt((hr + p['handle_fillet']) ** 2 -
                   (p['handle_fillet'] + p['thickness'] / 2) ** 2)
    outer_angle = math.degrees(math.atan2(hy - (back + p['handle_fillet']), -jx))
    ha = outer_angle + 180

    if reinforce['floor']:
        require(p['floor_rear_extra'] > 0 and p['floor_start'] > 0 and p['floor_ramp'] > 0,
                'floor_rear_extra / floor_start / floor_ramp phải dương.')
        require(p['floor_start'] + p['floor_ramp'] < cy,
                'floor_start + floor_ramp phải trước cy.')
        require(p['thickness'] + p['floor_rear_extra'] + p['floor_fillet'] < p['wall_height'],
                'Đáy gia cường quá cao so với thành.')
    if reinforce['handle']:
        require(p['brace_thickness'] > 0 and hr * 0.55 + p['brace_thickness'] / 2 < hr,
                'brace_thickness không vừa khoảng cán.')
        require(p['brace_reach'] > hr and p['brace_rise'] > 0,
                'brace_reach / brace_rise không hợp lệ.')
        require(p['wall_height'] + p['brace_rise'] < p['total_height'],
                'brace_rise vượt total_height.')
    if reinforce['walls']:
        require(p['wall_rib_width'] > 0 and p['wall_rib_radius'] > 0, 'wall_rib_* phải dương.')
        require(p['wall_rib_projection'] > 2 * p['wall_rib_radius'],
                'wall_rib_projection phải lớn hơn 2 * wall_rib_radius.')
        require(p['wall_height'] > 4 * p['wall_rib_radius'],
                'wall_height quá thấp cho gân thành.')
        require(p['depth'] * 0.25 + p['wall_rib_width'] / 2 < cy,
                'Gân thành quá gần góc sau.')
    if reinforce['rim']:
        require(abs(rim_z(cy, p) - p['wall_height']) < 1e-7,
                'rear rim requires both corner tangencies on the flat wall top')
        require(p['rim_projection'] > 0 and p['rim_height'] > 0, 'rim_* phải dương.')
        require(p['rim_height'] < p['wall_height'] and
                p['rim_height'] >= p['rim_projection'] + 0.5,
                'rim_height không hợp lệ.')
        require(p['rim_start'] > 0 and p['rim_taper'] > 0 and
                p['rim_start'] + p['rim_taper'] < p['depth'] - p['rear_radius'],
                'rim_start / rim_taper vượt thành bên.')

    x_min = -half - (p['rim_projection'] if reinforce['rim'] else 0)
    x_min = min(x_min, -half - (p['wall_rib_projection'] if reinforce['walls'] else 0))
    x_max = -x_min
    y_min = front
    y_max = hy + hr
    if reinforce['handle']:
        y_max = max(y_max, back + p['brace_reach'])
    if reinforce['rim']:
        y_max = max(y_max, back + p['rim_projection'])
    z_max = p['total_height']
    if reinforce['handle']:
        z_max = max(z_max, p['wall_height'] + p['brace_rise'])

    return {
        'half': half, 'front': front, 'back': back, 'hr': hr, 'hy': hy,
        'cx': cx, 'cy': cy, 'jx': jx, 'outer_angle': outer_angle, 'ha': ha,
        'inner_angle': math.degrees(math.atan2(
            hy - (back - p['thickness'] - p['handle_fillet']), -jx)),
        'bounds_mm': ((x_min, y_min, 0.0), (x_max, y_max, z_max)),
        'extents_mm': (x_max - x_min, y_max - y_min, z_max),
        'reinforce': reinforce,
    }

def rim_z(y, p):
    """SCAD rim_z: height of wall top / ramp at Y."""
    front = -p['depth'] / 2
    top = p['wall_height']
    bottom = 0.0
    ry = front + (p['wall_height'] + p['ramp_radius'] * (1 / math.cos(math.radians(p['ramp_angle'])) - 1)) / math.tan(
        math.radians(p['ramp_angle']))
    ty = ry - p['ramp_radius'] * math.sin(math.radians(p['ramp_angle']))
    if y < ty:
        return bottom + (y - front) * math.tan(math.radians(p['ramp_angle']))
    if y < ry:
        return top - p['ramp_radius'] + math.sqrt(p['ramp_radius'] ** 2 - (y - ry) ** 2)
    return top

def floor_lift(y, p):
    """Quintic rear floor lift used by reinforce_floor."""
    t = min(1.0, max(0.0, (y - p['floor_start']) / p['floor_ramp']))
    return p['floor_rear_extra'] * (6 * t ** 5 - 15 * t ** 4 + 10 * t ** 3)
