#include<assert.h>
#include<bits/stdc++.h>
long f(std::vector<long> nums, long val) {
    std::vector<long> new_list;
    for (long i : nums) {
        for (long j = 0; j < val; j++) {
            new_list.push_back(i);
        }
    }
    long sum = 0;
    for (long num : new_list) {
        sum += num;
    }
    return sum;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)10, (long)4})), (3)) == (42));
}
