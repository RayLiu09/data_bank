# - *- coding: utf-8 -*
import logging

class Watermark(object):
    """
    watermark, 提供各种数字水印技术工具

    实现思路说明：
    1. 图片水印技术，可用的有：基于最低有效位算法(LSB)的空间域方法，以及频域方法，如DCT域水印 - 基于JPEG压缩的DCT系数中嵌入水印；DWT域水印 - 在小波变换的不同子带中嵌入；DFT域水印 - 在傅里叶变换的幅度或相位中嵌入；
    2. 视频水印技术，帧内水印（每帧独立嵌入）；时序水印（利用帧间相关性）；压缩域水印（在H.264/HEVC码流中）；运动向量水印（在运动估计数据中）
    3. 音频水印技术，LSB编码，扩频水印 - 将水印信号扩展到整个频谱；回声隐藏 - 添加微秒级回声嵌入信息；相位编码 - 修改特定频段的相位信息；
    4. 文本水印技术,包括格式微调和Unicode水印，其中格式微调有：行间距调整，字间距调整，字体特征修改和同义词替换；Unicode水印有零宽度字符（即插入不可见的Unicode字符）和字符重排（使用特定的字符排列顺序）；
    """
    @staticmethod
    def lsb_embedding(img, watermark):
        """
        LSB嵌入水印
        :param img: 待嵌入水印的图片
        :param watermark: 水印
        :return: 嵌入水印的图片
        """
        pass
    @staticmethod
    def lsb_extract(img):
        """
        LSB提取水印
        :param img: 待提取水印的图片
        :return: 水印
        """
        pass
    @staticmethod
    def dct_embedding(img, watermark):
        """
        DCT嵌入水印
        :param img: 待嵌入水印的图片
        :param watermark: 水印
        :return: 嵌入水印的图片
        """
        pass
    @staticmethod
    def dct_extract(img):
        """
        DCT提取水印
        :param img: 待提取水印的图片
        :return: 水印
        """
        pass
    @staticmethod
    def dwt_embedding(img, watermark):
        """
        DWT嵌入水印
        :param img: 待嵌入水印的图片
        :param watermark: 水印
        :return: 嵌入水印的图片
        """
        pass
    @staticmethod
    def dwt_extract(img):
        """
        DWT提取水印
        :param img: 待提取水印的图片
        :return: 水印
        """
        pass
    @staticmethod
    def dft_embedding(img, watermark):
        """
        DFT嵌入水印
        :param img: 待嵌入水印的图片
        :param watermark: 水印
        :return: 嵌入水印的图片
        """
        pass
    @staticmethod
    def dft_extract(img):
        """
        DFT提取水印
        :param img: 待提取水印的图片
        :return: 水印
        """
        pass