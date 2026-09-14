#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums) {
    return nums[nums.size() / 2];
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-1, (long)-3, (long)-5, (long)-7, (long)0}))) == (-5));
}
