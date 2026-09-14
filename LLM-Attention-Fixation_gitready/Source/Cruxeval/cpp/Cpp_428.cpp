#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    for(int i = 0; i < nums.size(); i++) {
        if (!(i % 2)) {
            nums.push_back(nums[i] * nums[i + 1]);
        }
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
