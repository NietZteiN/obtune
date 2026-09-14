#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long p) {
    long prev_p = p - 1;
    if (prev_p < 0) {
        prev_p = nums.size() - 1;
    }
    return nums[prev_p];
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)6, (long)8, (long)2, (long)5, (long)3, (long)1, (long)9, (long)7})), (6)) == (1));
}
