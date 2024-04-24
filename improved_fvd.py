import math
from typing import List


class ImprovedFVD:
    r"""
    The Improved FVD model(modified).

    Usage: Initialize with args, then use ``self.result`` as the result.
    The result is calculated when accessing ``self.result`` attribute.

    LaTeX:
    ``a_n(t)=\alpha\{V[ΔX^{jq}_n(t)]-V_n(t)\}-\lambda_1\frac{d\vartheta_n(t)}{dt}+\lambda2\frac{d\phi_n(t)}{dt}``

    Based on Eq. ``(4)``, but we replaced ``\(\lambda_1\frac{d\vartheta_n(t)}{dt}+\lambda_2\frac{d\phi_n(t)}{dt}\)``
    with ``\(\lambda_1\frac{|\vartheta_n(t)-\vartheta_n(t-1)|}{\Delta t_{t,t-1}}+\lambda_2\frac{|\phi_n(t)-\phi_n(t-1)|}{\Delta t_{t,t-1}}\)``,
    where ``\(\vartheta_n(t-1)\)`` and ``\(\phi_n(t-1)\)`` are the data at the previous time point;
    ``\(\Delta t_{t,t-1}\)`` is the time difference from the previous frame to the current frame.
    Since trajectory data is usually composed of discrete data points and is not differentiable,
    thus this method is adopted to represent the rate of change of this variable over time.

    Based on following paper:

    Qi, W., Ma, S., & Fu, C. (2023).
    An improved car-following model considering the influence of multiple preceding vehicles in the same and two adjacent lanes.
    Physica A, 129356.
    https://doi.org/10.1016/j.physa.2023.129356
    """

    def __init__(
            self,
            alpha: float,
            lambda_1: float,
            lambda_2: float,
            v_1: float,
            v_2: float,
            c_1: float,
            c_2: float,
            p_2: float,
            p_3: float,
            q_2: float,
            q_3: float,
            s_2: float,
            s_3: float,

            current_car_current_frame: "CurrentCar",
            current_lane_front_cars_current_frame: List["CurrentLaneFrontCar"],

            frame_time_diff: float,

            current_car_last_frame: "CurrentCar",
            current_lane_front_cars_last_frame: List["CurrentLaneFrontCar"],

            p_1: float = 1,
            q_1: float = 1,
            s_1: float = 1,

            left_front_car_current_frame: "LeftFrontCar" = None,
            right_front_car_current_frame: "RightFrontCar" = None,

            left_front_car_last_frame: "LeftFrontCar" = None,
            right_front_car_last_frame: "RightFrontCar" = None,
    ):
        """

        :param current_car_current_frame:
        :param left_front_car_current_frame:
        :param right_front_car_current_frame:
        :param current_lane_front_cars_current_frame:
        :param args: ...
        """
        if not left_front_car_current_frame and not right_front_car_current_frame:
            p_2 = 0
            p_3 = 0
            q_2 = 0
            q_3 = 0
            s_2 = 0
            s_3 = 0
        elif not left_front_car_current_frame and right_front_car_current_frame:
            p_2 = 0
            q_2 = 0
            s_2 = 0
        elif left_front_car_current_frame and not right_front_car_current_frame:
            p_3 = 0
            q_3 = 0
            s_3 = 0

        if alpha > 2 or alpha < 0.05:
            raise ValueError('alpha must be between 0.05 and 2.')
        if lambda_1 > 40 or lambda_1 < 0 or lambda_2 > 40 or lambda_2 < 0:
            raise ValueError('lambdas must be between 0 and 40.')
        if q_1 + q_2 + q_3 != 1:
            raise ValueError('q_1 + q_2 + q_3 must be 1.')
        if s_1 + s_2 + s_3 != 1:
            raise ValueError('s_1 + s_2 + s_3 must be 1.')
        if sum(car.beta for car in current_lane_front_cars_current_frame) != 1:
            raise ValueError("Betas(impact probabilities) must have a sum of 1.")
        if p_1 + p_2 + p_3 != 1:
            raise ValueError("p_1 + p_2 + p_3 must be 1.")

        self.current_car_current_frame = current_car_current_frame
        self.left_front_car_current_frame = left_front_car_current_frame
        self.right_front_car_current_frame = right_front_car_current_frame
        self.current_lane_front_cars_current_frame = current_lane_front_cars_current_frame

        self.frame_time_diff = frame_time_diff

        self.current_car_last_frame = current_car_last_frame
        self.left_front_car_last_frame = left_front_car_last_frame
        self.right_front_car_last_frame = right_front_car_last_frame
        self.current_lane_front_cars_last_frame = current_lane_front_cars_last_frame

        self.alpha = alpha
        self.lambda_1 = lambda_1
        self.lambda_2 = lambda_2
        self.v_1 = v_1
        self.v_2 = v_2
        self.c_1 = c_1
        self.c_2 = c_2
        self.p_1 = p_1
        self.p_2 = p_2
        self.p_3 = p_3
        self.q_1 = q_1
        self.q_2 = q_2
        self.q_3 = q_3
        self.s_1 = s_1
        self.s_2 = s_2
        self.s_3 = s_3

        self._result = None

    @property
    def result(self):
        if self._result is None:
            self._result = self.__solve()
        return self._result

    class CarBase:
        r"""
        Assuming the directions are like this,
        as shown in Fig. 1. here and Fig. 1. in the paper::

            y
            ↑
            |        🚓f→                   Left lane
            | 🚕n→ 🚗n+1→ 🚗n+2→ ... 🚗n+m→  Current Lane
            |    🚙r→                       Right Lane
            +---------------------------> x
                Fig. 1. Like this.

                →    : Direction of the car
                🚕n   : Current car
                🚓f   : Left front car
                🚙r   : Right front car
                🚗n+k : Same lane front cars

        :param speed

        :param x

        :param y

        """

        def __init__(self, speed: float, x: float, y: float):
            self.speed = speed
            self.x = x
            self.y = y

    class CurrentCar(CarBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class FrontCarBase(CarBase):
        r"""
        Assuming the directions are like this,
        as shown in Fig. 1. here and Fig. 1. in the paper::

            y
            ↑
            |        🚓f→                   Left lane
            | 🚕n→ 🚗n+1→ 🚗n+2→ ... 🚗n+m→  Current Lane
            |    🚙r→                       Right Lane
            +---------------------------> x
                Fig. 1. Like this.

                →    : Direction of the car
                🚕n   : Current car
                🚓f   : Left front car
                🚙r   : Right front car
                🚗n+k : Same lane front cars

        :param current_car

        :param speed

        :param x

        :param y

        :param width

        :param length
        """

        def __init__(self, current_car, width: float, length: float, **kwargs):
            super().__init__(**kwargs)
            self.width = width
            self.length = length

            self.b = abs(current_car.y - self.y)
            """ The lateral distance """

            self.delta_x = abs(current_car.x - self.x)
            """ The longitudinal distance """

            self.theta = self.__calc_theta()
            """ The visual angle """

            self.varphi = self.__calc_varphi()
            """ The offset angle """

        def __calc_theta(self) -> float:
            r"""
            ``\theta_k(t)=\arctan\frac{b_{n,k}(t)+w_k/2}{Δx_{n,k}(t)-l_k}-\arctan\frac{b_{n,k}(t)-w_k/2}{Δx_{n,k}(t)-l_k}``
            ``(2)``

            :return: ``\theta_k(t)``
            """
            return math.atan(
                (self.b + self.width / 2)
                /
                (self.delta_x - self.length)
            ) - math.atan(
                (self.b - self.width / 2)
                /
                (self.delta_x - self.length)
            )

        def __calc_varphi(self) -> float:
            r"""
            ``\varphi_k(t)=\arctan\frac{b_{n,k}(t)}{Δx_{n,k}(t)-l_k}``
            ``(3)``

            :return: ``\varphi_k(t)``
            """
            return math.atan(
                self.b
                /
                (self.delta_x - self.length)
            )

    class CurrentLaneFrontCar(FrontCarBase):
        def __init__(self, beta: float, **kwargs):
            super().__init__(**kwargs)
            self.beta = beta
            """ Impact probability """

    class LeftFrontCar(FrontCarBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    class RightFrontCar(FrontCarBase):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)

    def __weighted_visual_angle(
            self,
            current_lane_front_cars: List[CurrentLaneFrontCar],
            left_front_car: LeftFrontCar | None,
            right_front_car: RightFrontCar | None
    ) -> float:
        r"""
        ``\vartheta_n(t)=q_1\theta_{n+1}(t)+q_2\theta_f(t)+q_3\theta_r(t)``
        ``(6)``
        :return:
        """
        return self.q_1 * current_lane_front_cars[0].theta + \
               self.q_2 * left_front_car.theta if left_front_car else 0 + \
                                                                      self.q_3 * right_front_car.theta if right_front_car else 0

    def __weighted_visual_angle_current_frame(self):
        return self.__weighted_visual_angle(
            self.current_lane_front_cars_current_frame,
            self.left_front_car_current_frame,
            self.right_front_car_current_frame,
        )

    def __weighted_visual_angle_last_frame(self):
        return self.__weighted_visual_angle(
            self.current_lane_front_cars_last_frame,
            self.left_front_car_last_frame,
            self.right_front_car_last_frame,
        )

    def __weighted_offset_angle(
            self,
            current_lane_front_cars: List[CurrentLaneFrontCar],
            left_front_car: LeftFrontCar,
            right_front_car: RightFrontCar
    ) -> float:
        r"""
        ``\phi_n(t)=s_1\varphi_{n+1}(t)+s_2\varphi_f(t)+s_3\varphi_r(t)``
        ``(7)``
        :return:
        """
        return self.s_1 * current_lane_front_cars[0].varphi + \
               self.s_2 * left_front_car.varphi if left_front_car else 0 + \
               self.s_3 * right_front_car.varphi if right_front_car else 0

    def __weighted_offset_angle_current_frame(self):
        return self.__weighted_offset_angle(
            self.current_lane_front_cars_current_frame,
            self.left_front_car_current_frame,
            self.right_front_car_current_frame,
        )

    def __weighted_offset_angle_last_frame(self):
        return self.__weighted_offset_angle(
            self.current_lane_front_cars_last_frame,
            self.left_front_car_last_frame,
            self.right_front_car_last_frame,
        )

    def __weighted_headway(self):
        r"""
        ``ΔX^{jq}_n(t)=p_1\sum^m_{j=1}\left(\beta_j\frac{b_{n,j}(t)}{\tan\varphi_j(t)}\right)+p_2\frac{b_{n,f}(t)}{\tan\varphi_f(t)}+p_3\frac{b_{n,r}(t)}{\tan\varphi_r(t)}
        ``(5)``

        :return:
        """
        result = 0
        for car in self.current_lane_front_cars_current_frame:
            result += car.beta * (car.b / math.tan(car.varphi))
        result *= self.p_1

        result += self.p_2 * (
                self.left_front_car_current_frame.b / math.tan(self.left_front_car_current_frame.varphi)
        ) if self.left_front_car_current_frame else 0

        result += self.p_3 * (
                self.right_front_car_current_frame.b / math.tan(self.right_front_car_current_frame.varphi)
        ) if self.right_front_car_last_frame else 0

        return result

    def __optimized_velocity_function(self) -> float:
        r"""
        ``V\left[ΔX_n^{jq}(t)\right]=V_1+V_2\tanh{[C_1(weighted\ headway)-C_2]}``
        ``(8)``

        :return:
        """
        return self.v_1 + self.v_2 * math.tanh(self.c_1 * self.__weighted_headway() - self.c_2)

    def __solve(self) -> float:
        r"""
        ``a_n(t)=\alpha\{V[ΔX^{jq}_n(t)]-V_n(t)\}-\lambda_1\frac{d\vartheta_n(t)}{dt}+\lambda2\frac{d\phi_n(t)}{dt}``

        Based on ``(4)``

        :return: ``a_n(t)``
        """
        return self.alpha * (
                self.__optimized_velocity_function() - self.current_car_current_frame.speed
        ) - self.lambda_1 * abs(
            (self.__weighted_visual_angle_current_frame() - self.__weighted_visual_angle_last_frame())
            /
            self.frame_time_diff
        ) + self.lambda_2 * abs(
            (self.__weighted_offset_angle_current_frame() - self.__weighted_offset_angle_last_frame())
            /
            self.frame_time_diff
        )
