import math
import random
from collections import defaultdict


class Prize:
    def __init__(self, name, total, sections):
        self.name = name
        self.original = total
        self.remaining = total
        self.sections = sections
        self.probability = 0.0

    def __repr__(self):
        return f"{self.name}({self.remaining}/{self.original})"


class LotterySystem:
    def __init__(self):
        self.prizes = [
            Prize("一等奖", 5, 1),
            Prize("二等奖", 10, 1),
            Prize("三等奖", 1500, 2),
            Prize("四等奖", 100, 1),
            Prize("五等奖", 300, 1),
            Prize("幸运奖", 1000, 2),
        ]
        self.total_days = 2.5
        self.current_day = 1.0
        self.periods = self.generate_schedule()
        self.first_prize_limits = defaultdict(lambda: {'morning': 1, 'afternoon': 1})
        self.carry_over = 0
        self.daily_participants = 1500  # 首日预估人数
        self.actual_participants = {}  # 记录每日实际人数

    def generate_schedule(self):
        """生成时间表：2.5天分解为5个时段"""
        return [
            {'day': 1.0, 'period': 'morning'},
            {'day': 1.5, 'period': 'afternoon'},
            {'day': 2.0, 'period': 'morning'},
            {'day': 2.5, 'period': 'afternoon'},
            {'day': 3.0, 'period': 'morning'}
        ]

    def print_status(self, stage, draw_info):
        """打印详细状态信息"""
        print(f"\n【{stage}】第{draw_info['day']}天 {draw_info['period']}时段 "
              f"第{draw_info['draw_num']}次抽奖")
        print("奖品名称 | 剩余数量 | 当前概率")
        for p in self.prizes:
            print(f"{p.name.ljust(6)} | {p.remaining:8} | {p.probability * 100:6.2f}%")
        if stage == "抽奖结果":
            print(f"本次中奖：{draw_info['won_prize']}")

    def replenish_third_prize(self):
        """三等奖库存补充机制"""
        third = next(p for p in self.prizes if p.name == "三等奖")
        threshold = math.ceil(third.original * 0.1)
        if third.remaining < threshold:
            need = threshold - third.remaining
            third.remaining += need
            print(f"\n※※※ 运营通知：三等奖补充{need}个，当前库存：{third.remaining} ※※※")

    def calculate_probabilities(self, current_time):
        """动态概率计算引擎"""
        remaining_days = max(0.01, self.total_days - (current_time - 1))

        # 重置概率并计算有效奖品
        valid_prizes = []
        total_raw_prob = 0
        for p in self.prizes:
            if p.remaining <= 0:
                p.probability = 0.0
                continue

            # 每日目标
            daily_target = math.ceil(p.remaining / remaining_days)
            # 动态权重
            dynamic_weight = 1 + (p.remaining / p.original) * (self.total_days / remaining_days)
            # 基础概率
            base_prob = daily_target / self.daily_participants
            # 最终原始概率
            raw_prob = base_prob * dynamic_weight

            p.probability = raw_prob
            total_raw_prob += raw_prob
            valid_prizes.append(p)

        # 概率压缩
        if total_raw_prob > 1:
            compress = 1 / total_raw_prob
            for p in valid_prizes:
                p.probability *= compress

        # 转盘八等份分配
        total_section_prob = 0
        section_probs = {}
        for p in valid_prizes:
            section_ratio = p.sections / 8
            section_prob = p.probability * section_ratio
            section_probs[p.name] = section_prob
            total_section_prob += section_prob

        # 归一化处理
        if total_section_prob > 0:
            for p in valid_prizes:
                p.probability = section_probs[p.name] / total_section_prob

    def enforce_first_prize_rules(self, current_time):
        """一等奖限额管理"""
        day = math.floor(current_time)
        period = 'morning' if (current_time % 1) == 0 else 'afternoon'
        first_prize = next(p for p in self.prizes if p.name == "一等奖")

        # 新的一天重置限额
        if period == 'morning':
            self.first_prize_limits[day][period] = 1 + self.carry_over
            self.carry_over = 0

        # 下午时段调整限额
        if period == 'afternoon' and self.first_prize_limits[day]['morning'] > 0:
            self.first_prize_limits[day][period] = 2

    def run_simulation(self):
        """主运行逻辑"""
        for period_info in self.periods:
            current_time = period_info['day']
            day_num = math.floor(current_time)
            period = period_info['period']

            # 更新预估参与人数
            if day_num > 1:
                self.daily_participants = self.actual_participants.get(day_num - 1, 1500)

            # 计算本时段抽奖次数
            max_draws = self.daily_participants // 2 if period == 'morning' else self.daily_participants // 2
            if current_time == 3.0:  # 最后半天
                max_draws = math.ceil(self.daily_participants * 0.5)

            self.enforce_first_prize_rules(current_time)

            for draw_num in range(1, max_draws + 1):
                # 跳过无效抽奖
                if all(p.remaining <= 0 for p in self.prizes):
                    print("所有奖品已抽空！")
                    return

                # 概率计算
                self.calculate_probabilities(current_time)
                self.replenish_third_prize()

                # 打印抽奖前状态
                self.print_status("抽奖前", {
                    'day': day_num,
                    'period': period,
                    'draw_num': draw_num
                })

                # 准备可用奖品
                available_prizes = []
                weights = []
                for p in self.prizes:
                    if p.probability > 0 and p.remaining > 0:
                        # 处理一等奖限额
                        if p.name == "一等奖":
                            if self.first_prize_limits[day_num][period] <= 0:
                                continue
                        available_prizes.append(p)
                        weights.append(p.probability)

                # 执行抽奖
                selected = random.choices(available_prizes, weights=weights, k=1)[0]
                selected.remaining -= 1
                if selected.name == "一等奖":
                    self.first_prize_limits[day_num][period] -= 1

                # 记录抽奖结果
                self.actual_participants.setdefault(day_num, 0)
                self.actual_participants[day_num] += 1

                # 打印抽奖后状态
                self.print_status("抽奖结果", {
                    'day': day_num,
                    'period': period,
                    'draw_num': draw_num,
                    'won_prize': selected.name
                })

                # 处理当日未使用的一等奖配额
                if period == 'afternoon' and selected.name != "一等奖":
                    self.carry_over = self.first_prize_limits[day_num][period]


if __name__ == "__main__":
    print("智能抽奖系统启动".center(50, "="))
    system = LotterySystem()
    system.run_simulation()

    print("\n最终统计：")
    for p in system.prizes:
        print(f"{p.name.ljust(6)} 已发放：{p.original - p.remaining} 剩余：{p.remaining}")
    print(f"实际参与人数统计：{dict(system.actual_participants)}")