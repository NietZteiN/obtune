#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = nums.size() / 2;
    for (int i = 0; i < count; i++) {
        nums.erase(nums.begin());
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)4, (long)1, (long)2, (long)3}))) == (std::vector<long>({(long)1, (long)2, (long)3})));
}
