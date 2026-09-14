#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long n) {
    long result = nums[n];
    nums.erase(nums.begin() + n);
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-7, (long)3, (long)1, (long)-1, (long)-1, (long)0, (long)4})), (6)) == (4));
}
