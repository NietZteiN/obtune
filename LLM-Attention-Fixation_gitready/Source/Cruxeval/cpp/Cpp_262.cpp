#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<long> nums) {
    int count = nums.size();
    std::unordered_map<int, std::string> score = {{0, "F"}, {1, "E"}, {2, "D"}, {3, "C"}, {4, "B"}, {5, "A"}, {6, ""}};
    std::vector<std::string> result;
    for (int i = 0; i < count; i++) {
        result.push_back(score[nums[i]]);
    }
    return std::accumulate(result.begin(), result.end(), std::string(""));
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)4, (long)5}))) == ("BA"));
}
