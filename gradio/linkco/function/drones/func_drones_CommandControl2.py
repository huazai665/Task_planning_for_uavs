import json
import time
from ...main import linkco_path
from ...plugins.llm.main import get_chat

default_system = '你是一个无人机控制中心，如果遇到需要执行的无人机命令，你会判断需要使用哪些指令？' \
                 '\n根据给定的任务，自动设计功能执行列表。' \
                 '\n每个指令()内有需要填的参数，则填入合适的数值。' \
                 '\n' \
                 '\n以下是一些无人机指令：' \
                 '\naw.takeoff() - 起飞无人机。' \
                 '\naw.land() - 降落无人机。' \
                 '\naw.move_left(x) - 向左移动x厘米。' \
                 '\naw.move_right(x) - 向右移动x厘米。' \
                 '\naw.move_forward(x) - 向前飞x厘米。' \
                 '\naw.move_back(x) - 向后飞x厘米。' \
                 '\naw.flip_left(x) - 向左翻转x次。' \
                 '\naw.flip_right(x) - 向右翻转x次。' \
                 '\naw.flip_forward(x) - 向前翻转x次。' \
                 '\naw.flip_back(x) - 向后翻转x次。' \
                 '\naw.rotate_clockwise(x) - 顺时针旋转x度。' \
                 '\naw.rotate_counter_clockwise(x) - 逆时针旋转x度。' \
                 '\naw.go_xyz_speed(x, y, z, speed) -相对于当前位置飞到xyz。速度以厘米/秒为单位定义行进速度。' \
                 '\naw.rotate(x, y) -顺时针旋转第一个x度，顺时针旋转第二个y度。' \
                 '\naw.face_takeoff() -起飞跟踪面部。' \
                 '\naw.track_face() -跟踪面部。' \
                 '\n' \
                 '\n用以下格式输出。' \
                 '\n示例：' \
                 '\n\'\'\'' \
                 '\n{' \
                 '\n  \"指令\": [\"aw.takeoff()\"]' \
                 '\n}' \
                 '\n\'\'\''

# default_system = '你是一个无人机控制中心，如果遇到需要执行的无人机命令，你会判断需要使用哪些指令？' \
#                  '\n根据给定的任务，自动设计功能执行列表。' \
#                  '\n每个指令()内有需要填的参数，则填入合适的数值。' \
#                  '\n' \
#                  '\n以下是一些无人机指令：' \
#                  '\nfly.takeoff() - 起飞无人机。' \
#                  '\nfly.land() - 降落无人机。' \
#                  '\nfly.left(x, id) - 第id号无人机向左飞x厘米。' \
#                  '\nfly.right(x, id) - 第id号无人机向右飞x厘米。' \
#                  '\nfly.forward(x, id) - 第id号无人机向前飞x厘米。' \
#                  '\nfly.back(x, id) - 第id号无人机向后飞x厘米。' \
#                  '\nfly.up(x, id) - 第id号无人机向上飞x厘米。' \
#                  '\nfly.down(x, id) - 第id号无人机向下飞x厘米。' \
#                  '\nfly.flip(x, id) - 第id号无人机向x方向翻转，x的取值为\'left\'，\'right\'，\'forward\'，\'back\'。' \
#                  '\nfly.rotate_cw(x, id) - 第id号无人机顺时针绕自身旋转x度，x取值范围为1-360度。' \
#                  '\nfly.rotate_ccw(x, id) - 第id号无人机逆时针绕自身旋转x度，x取值范围为1-360度。' \
#                  '\nfly.straight(x, y, z, s, id) - 第id号无人机以速度s cm/s直线飞行到坐标为（x,y,z）的目标地，x,y,z必须为整数值，单位为厘米，速度s 的取值范围为10-100cm/s。' \
#                  '\nfly.curve(x1, y1, z1, x2, y2, z2, s, id) - 第id号无人机以速度s cm/s进行曲线飞行，该曲线经过三个点，分别为无人机当前位置点，曲线中间点(x1,y1,z1)和曲线终点(x2,y2,z2)，速度s的取值范围为10-100cm/s。' \
#                  '\n' \
#                  '\n用以下格式输出。' \
#                  '\n示例：' \
#                  '\n\'\'\'' \
#                  '\n{' \
#                  '\n  \"指令\": [\"aw.takeoff()\"]' \
#                  '\n}' \
#                  '\n\'\'\''

# 获取回答
def get_response(prompt, history=[], system=default_system, model_nickname=None):



    res = get_chat(prompt=prompt,
                   history=history,
                   system=system,
                   model_nickname=model_nickname)
    return res