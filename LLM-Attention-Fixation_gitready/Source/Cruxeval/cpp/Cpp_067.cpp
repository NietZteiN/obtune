#include<assert.h>
#include<bits/stdc++.h>
std::string f(long num1, long num2, long num3) {
    std::vector<long> nums = {num1, num2, num3};
    std::sort(nums.begin(), nums.end());
    return std::to_string(nums[0]) + "," + std::to_string(nums[1]) + "," + std::to_string(nums[2]);
}
int main() {
    auto candidate = f;
    assert(candidate((6), (8), (8)) == ("6,8,8"));
}
