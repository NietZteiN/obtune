#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    int count = 0;
    while(!nums.empty()) {
        if(count % 2 == 0) {
            nums.pop_back();
        } else {
            nums.erase(nums.begin());
        }
        count++;
    }
    return nums;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)3, (long)2, (long)0, (long)0, (long)2, (long)3}))) == (std::vector<long>()));
}
