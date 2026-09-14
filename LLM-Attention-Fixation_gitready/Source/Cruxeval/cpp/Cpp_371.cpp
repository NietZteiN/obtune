#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums) {
    nums.erase(std::remove_if(nums.begin(), nums.end(), [](int x) { return x % 2 != 0; }), nums.end());
    
    long sum_ = 0;
    for (int num : nums) {
        sum_ += num;
    }
    return sum_;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)11, (long)21, (long)0, (long)11}))) == (0));
}
