import math
import torch
import torch.nn as nn
import block as B

import pdb

class RRDB_Net(nn.Module):
    def __init__(self, in_nc=3, out_nc=3, nf=64, nb=23, gc=32, upscale=4, norm_type=None, act_type='leakyrelu', \
            mode='CNA', res_scale=1, upsample_mode='upconv'):
        super(RRDB_Net, self).__init__()
        # in_nc = 3
        # out_nc = 3
        # nf = 64
        # nb = 23
        # gc = 32
        # upscale = 4
        # norm_type = None
        # act_type = 'leakyrelu'
        # mode = 'CNA'
        # res_scale = 1
        # upsample_mode = 'upconv'

        n_upscale = int(math.log(upscale, 2))
        if upscale == 3:
            n_upscale = 1

        fea_conv = B.conv_block(in_nc, nf, kernel_size=3, norm_type=None, act_type=None)
        rb_blocks = [B.RRDB(nf, kernel_size=3, gc=32, stride=1, bias=True, pad_type='zero', \
            norm_type=norm_type, act_type=act_type, mode='CNA') for _ in range(nb)]
        LR_conv = B.conv_block(nf, nf, kernel_size=3, norm_type=norm_type, act_type=None, mode=mode)

        if upsample_mode == 'upconv':
            upsample_block = B.upconv_blcok
        elif upsample_mode == 'pixelshuffle':
            upsample_block = B.pixelshuffle_block
        else:
            raise NotImplementedError('upsample mode [%s] is not found' % upsample_mode)
        if upscale == 3:
            upsampler = upsample_block(nf, nf, 3, act_type=act_type)
        else:
            upsampler = [upsample_block(nf, nf, act_type=act_type) for _ in range(n_upscale)]
        HR_conv0 = B.conv_block(nf, nf, kernel_size=3, norm_type=None, act_type=act_type)
        HR_conv1 = B.conv_block(nf, out_nc, kernel_size=3, norm_type=None, act_type=None)

        self.model = B.sequential(fea_conv, B.ShortcutBlock(B.sequential(*rb_blocks, LR_conv)),\
            *upsampler, HR_conv0, HR_conv1)

        # self = RRDB_Net(
        #   (model): Sequential(
        #     (0): Conv2d(3, 64, kernel_size=(3, 3), stride=(1, 1), padding=(1, 1))
        #     (1): Identity + 
        #     |Sequential(
        #     |  (0): RRDB(
        #     |    (RDB1): ResidualDenseBlock_5C(
        #     |      (noise): GaussianNoise()



    def forward(self, x):
        # x.size() -- [1, 3, 64, 64], [0.0, 1.0]
        x = self.model(x)
        return x.clamp(0.0, 1.0)
