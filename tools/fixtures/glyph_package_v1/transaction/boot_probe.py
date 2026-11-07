"""Extract production startup bodies; hardware boundaries are explicit host stubs."""
def function(text, name, result='void'):
    start = text.index(result+' '+name+'(')
    at = text.index('{', start)+1
    depth = 1
    while depth:
        depth += (text[at] == '{')-(text[at] == '}')
        at += 1
    return text[start:at]

def extract(repo, out):
    text = (repo/'config/glyph/common/src/config.cpp').read_text()
    names = [('draw_recovery_page','void'),('show_boot_stage','void'),('enter_recovery_configurator','void'),
             ('MigrateBootLegacyConfiguration','bool'),('setup','void')]
    out.write_text('\n'.join(function(text,n,t) for n,t in names)+'\n')
