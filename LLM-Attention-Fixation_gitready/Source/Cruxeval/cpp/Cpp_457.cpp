#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    while (nums.size()>0) 
        nums.pop_back();
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)1, (long)7, (long)5, (long)6}))) == (std::vector<long>()));
}
