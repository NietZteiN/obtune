#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long index) {
    long result = nums[index] % 42 + nums[index] * 2;
    nums.erase(nums.begin() + index);
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)2, (long)0, (long)3, (long)7})), (3)) == (9));
}
