#include<assert.h>
#include<bits/stdc++.h>
std::tuple<std::vector<long>, std::vector<long>> f(std::vector<long> nums, long target) {
    std::vector<long> lows, higgs;
    for (long i : nums) {
        if (i < target) {
            lows.push_back(i);
        } else {
            higgs.push_back(i);
        }
    }
    lows.clear();
    return std::make_tuple(lows, higgs);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)12, (long)516, (long)5, (long)2, (long)3, (long)214, (long)51})), (5)) == (std::make_tuple(std::vector<long>(), std::vector<long>({(long)12, (long)516, (long)5, (long)214, (long)51}))));
}
