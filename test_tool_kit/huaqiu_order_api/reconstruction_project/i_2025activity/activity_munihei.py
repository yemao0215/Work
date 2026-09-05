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


class LotterySimulator:
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
        self.daily_participants = 1500
        self.first_prize_limit = {'morning': 1, 'afternoon': 1}
        self.carry_over = 0
        self.periods = [
            {'day': 1, 'period': 'morning', 'draws': 750},
            {'day': 1, 'period': 'afternoon', 'draws': 750},
            {'day': 2, 'period': 'morning', 'draws': 750},
            {'day': 2, 'period': 'afternoon', 'draws': 750},
            {'day': 3, 'period': 'morning', 'draws': 375},
        ]

    def print_status(self, prefix, draw_info):
        print(f"\n【{prefix}】第{draw_info['day']}天 {draw_info['period']} 第{draw_info['draw_num']}次抽奖")
        for p in self.prizes:
            print(f"{p.name.ljust(5)}：概率={p.probability * 100:6.2f}% 剩余={p.remaining:4}")
        if prefix == "抽奖结果":
            print(f"本次中奖：{draw_info['won_prize']}")

    def check_and_replenish(self):
        third = next(p for p in self.prizes if p.name == "三等奖")
        threshold = math.ceil(third.original * 0.1)
        if third.remaining < threshold:
            need = threshold - third.remaining
            third.remaining += need
            print(f"\n【库存补充】三等奖补充{need}个，当前库存：{third.remaining}")

    def calculate_probabilities(self, remaining_days):
        total_raw_prob = 0
        valid_prizes = []

        # 计算基础概率和动态权重
        for p in self.prizes:
            if p.remaining <= 0:
                p.probability = 0.0
                continue

            # 每日目标
            daily_target = math.ceil(p.remaining / remaining_days) if remaining_days > 0 else 0
            # 动态权重
            dynamic_weight = 1 + (p.remaining / p.original) * (self.total_days / remaining_days)
            # 基础概率
            base_prob = daily_target / self.daily_participants
            # 最终概率
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
        for p in valid_prizes:
            section_prob = p.probability * p.sections / 8
            p.probability = section_prob
            total_section_prob += section_prob

        # 归一化处理
        if total_section_prob > 0:
            for p in valid_prizes:
                p.probability /= total_section_prob

    def adjust_first_prize_limit(self, current_day, period):
        first = next(p for p in self.prizes if p.name == "一等奖")

        # 新的一天重置限额
        if period == 'morning' and not hasattr(self, 'last_day'):
            self.first_prize_limit = {'morning': 1, 'afternoon': 1}
            first.remaining += self.carry_over
            self.carry_over = 0
            self.last_day = current_day

    def run_single_draw(self, draw_info):
        # 计算剩余天数
        elapsed_days = (draw_info['day'] - 1) + (0.5 if draw_info['period'] == 'afternoon' else 0)
        remaining_days = max(0.01, self.total_days - elapsed_days)  # 防止除零

        # 计算概率
        self.calculate_probabilities(remaining_days)

        # 打印抽奖前状态
        self.print_status("抽奖前", draw_info)

        # 执行抽奖
        available_prizes = [p for p in self.prizes if p.probability > 0 and p.remaining > 0]
        weights = [p.probability for p in available_prizes]
        selected = random.choices(available_prizes, weights=weights, k=1)[0]

        # 处理一等奖限额
        if selected.name == "一等奖":
            self.first_prize_limit[draw_info['period']] -= 1

        # 更新库存
        selected.remaining -= 1

        # 检查库存补充
        self.check_and_replenish()

        # 打印抽奖结果
        self.print_status("抽奖结果", {
            **draw_info,
            'won_prize': selected.name
        })

    def simulate(self):
        for period_info in self.periods:
            day = period_info['day']
            period = period_info['period']
            self.adjust_first_prize_limit(day, period)

            for draw_num in range(1, period_info['draws'] + 1):
                self.run_single_draw({
                    'day': day,
                    'period': period,
                    'draw_num': draw_num
                })

                # 提前终止检查
                if all(p.remaining <= 0 for p in self.prizes if p.name not in ["三等奖", "幸运奖"]):
                    print("\n所有重要奖品已抽完，活动提前结束")
                    return

        # 处理剩余一等奖顺延
        first = next(p for p in self.prizes if p.name == "一等奖")
        self.carry_over = first.remaining
        print(f"\n活动结束，一等奖剩余顺延数量：{self.carry_over}")


if __name__ == "__main__":
    print("抽奖模拟开始".center(50, "="))
    simulator = LotterySimulator()
    simulator.simulate()

    print("\n最终库存统计：")
    for p in simulator.prizes:
        print(f"{p.name.ljust(5)}：已抽中{p.original - p.remaining:4} 剩余：{p.remaining:4}")