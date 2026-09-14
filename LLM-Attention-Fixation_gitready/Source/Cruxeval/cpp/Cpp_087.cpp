#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<long> nums) {
    std::reverse(nums.begin(), nums.end());
    std::stringstream ss;
    for (int num : nums) {
        ss << num;
    }
    return ss.str();
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)9, (long)3, (long)1, (long)-2}))) == ("-2139-1"));
}
