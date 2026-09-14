#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::tuple<long, long>> f(std::vector<long> nums) {
    std::vector<std::tuple<long, long>> output;
    for (long n : nums) {
        output.push_back(std::make_tuple(std::count(nums.begin(), nums.end(), n), n));
    }
    std::sort(output.begin(), output.end(), std::greater<>());
    return output;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)1, (long)3, (long)1, (long)3, (long)1}))) == (std::vector<std::tuple<long, long>>({(std::tuple<long, long>)std::make_tuple(4, 1), (std::tuple<long, long>)std::make_tuple(4, 1), (std::tuple<long, long>)std::make_tuple(4, 1), (std::tuple<long, long>)std::make_tuple(4, 1), (std::tuple<long, long>)std::make_tuple(2, 3), (std::tuple<long, long>)std::make_tuple(2, 3)})));
}
