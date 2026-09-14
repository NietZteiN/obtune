#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = 1;
    for (int i = count; i < nums.size() - 1; i += 2) {
        nums[i] = std::max(nums[i], nums[count-1]);
        count++;
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3}))) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
