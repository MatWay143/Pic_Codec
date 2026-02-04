from encoding.stereo.grayscale.gs_s_e import grayscale_stereo_encode
from encoding.stereo.multi.mc_s_e import multicolor_stereo_encode
from encoding.stereo.bw.bw_s_e import bnw_stereo_encode
from encoding.mono.grayscale.gs_m_e import grayscale_mono_encode
from encoding.mono.multi.mc_m_e import multicolor_mono_encode
from encoding.mono.bw.bw_m_e import bnw_mono_encode
from decoding.stereo.grayscale.gs_s_d import grayscale_stereo_decode
from decoding.stereo.multi.mc_s_d import multicolor_stereo_decode
from decoding.stereo.bw.bw_s_d import bnw_stereo_decode
from decoding.mono.grayscale.gs_m_d import grayscale_mono_decode
from decoding.mono.multi.mc_m_d import multicolor_mono_decode
from decoding.mono.bw.bw_m_d import bnw_mono_decode

def func_manager(path1, path2, properties, code):
    if code==111:
        bnw_stereo_encode(path1, path2, properties)
    elif code==112:
        grayscale_stereo_encode(path1, path2, properties)
    elif code==113:
        multicolor_stereo_encode(path1, path2, properties)
    elif code==121:
        bnw_mono_encode(path1, properties)
    elif code==122:
        grayscale_mono_encode(path1, properties)
    elif code==123:
        multicolor_mono_encode(path1, properties)
    elif code==211:
        bnw_stereo_decode(path1, path2, properties)
    elif code==212:
        grayscale_stereo_decode(path1, path2, properties)
    elif code==213:
        multicolor_stereo_decode(path1, path2)
    elif code==221:
        bnw_mono_decode(path1, properties)
    elif code==222:
        grayscale_mono_decode(path1, properties)
    elif code==223:
        multicolor_mono_decode(path1, properties)