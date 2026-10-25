import sys,json,unittest
from pathlib import Path
snapshot=Path(sys.argv[1]);current=Path(sys.argv[2]);sys.path.insert(0,str(snapshot/'tools'))
import test_kazuya_profile_v4 as suite
import check_glyph_profile_native_ultimate as native
import check_glyph_stage_b_ultimate_profiles as stage_b
native.ROOT=current;native.HOST=current/'tools/fixtures/profile_native_ultimate';native.NANOPB=current/'.pio/libdeps/glyph_mk6/Nanopb'
suite.SOURCE=current/'profiles/kazuya/Kazuya.profile.json';suite.base.SOURCE=suite.SOURCE
result=unittest.TextTestRunner(verbosity=2).run(unittest.defaultTestLoader.loadTestsFromTestCase(suite.KazuyaV4Tests))
Path(sys.argv[3]).write_text(json.dumps({'status':'PASS' if result.wasSuccessful() else 'FAIL','tests_run':result.testsRun,'observations':suite.KazuyaV4Tests.observations,'canonical_source':str(suite.SOURCE),'production_cpp_root':str(native.ROOT),'expectation_snapshot':'5e30341ee06761e20e864ccc013ca6658e42b5ca'},indent=2)+'\n')
raise SystemExit(0 if result.wasSuccessful() and result.testsRun==11 else 1)
