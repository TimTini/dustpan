"""Offline source/geometry contract; no local work payload is required."""
import importlib.util
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'fusion/Dustpan'))
spec=importlib.util.spec_from_file_location('dustpan_builder',ROOT/'fusion/Dustpan/Dustpan.py')
model=importlib.util.module_from_spec(spec);spec.loader.exec_module(model)

class GeometryContract(unittest.TestCase):
    def test_source_hash_and_defaults_match(self):
        import hashlib,re
        source=(ROOT/'dustpan.scad').read_bytes()
        self.assertEqual(hashlib.sha256(source).hexdigest(),model.SOURCE_SHA256)
        values=dict(re.findall(r'^([a-z_]+) = ([-0-9.]+);',source.decode('utf-8'),re.M))
        for name,number in model.DEFAULTS.items():
            expected=0.1*float(values['depth']) if name=='floor_start' else float(values[name])
            self.assertAlmostEqual(number,expected,msg=name)

    def test_pad_cap_overlap_stays_inside_wall(self):
        self.assertAlmostEqual(model._geo.pad_cap(model.DEFAULTS),9.7)
        p=model.resolve_parameters({'wall_height':9.4})
        self.assertGreater(model._geo.pad_cap(p),9.2)
        self.assertLess(model._geo.pad_cap(p),9.4)

    def test_floor_transition_is_built_from_quintic_sections(self):
        sections=model.floor_sections(model.DEFAULTS)
        self.assertEqual(len(sections),26)
        self.assertAlmostEqual(sections[0][0],20)
        self.assertAlmostEqual(sections[-1][0],50.5)
        for y,path in sections:
            points=model.sample_path(path)
            self.assertAlmostEqual(min(z for x,z in points),2.5)
            expected=3+model.floor_lift(y,model.DEFAULTS)
            self.assertTrue(any(abs(z-expected)<1e-8 for x,z in points))
    def test_outer_profile_handle_is_single_symmetric_arc(self):
        path=model.outer_path(model.DEFAULTS)
        arcs=[s for s in path if s[0]=='arc' and s[2]==10]
        self.assertEqual(len(arcs),1)
    def test_rim_triangles_follow_original_ramp(self):
        sections=model.rim_sections(model.DEFAULTS)
        self.assertEqual(len(sections),49)
        for y,path in sections:
            z=max(q[1] for q in model.sample_path(path))
            self.assertAlmostEqual(z,model.rim_z(y,model.DEFAULTS))
    def test_floor_start_is_derived_for_scaled_rebuild(self):
        p=model.resolve_parameters({'width':220,'depth':220,'thickness':4,'total_height':270})
        self.assertEqual(p['floor_start'],22)
        self.assertEqual(model.floor_sections(p)[0][0],22)
    def test_rounded_rib_has_three_tangent_arcs(self):
        path=model.rib_path(model.DEFAULTS)
        self.assertEqual(sum(s[0]=='arc' for s in path),3)
        pts=model.sample_path(path)
        self.assertAlmostEqual(min(z for x,z in pts),0)
        self.assertAlmostEqual(max(x for x,z in pts),103,places=2)
    def test_invalid_flat_corner_contract(self):
        with self.assertRaises(ValueError):
            model.layout(model.resolve_parameters({'depth':100}),{'floor':False,'handle':False,'walls':False,'rim':True})

if __name__=='__main__':unittest.main()
