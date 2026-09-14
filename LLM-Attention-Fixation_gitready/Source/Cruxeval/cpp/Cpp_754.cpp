#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> nums) {
    int width = std::stoi(nums[0]);
    std::vector<std::string> result;
    for (size_t i = 1; i < nums.size(); ++i) {
        std::string val = nums[i];
        while (val.size() < width) {
            val = "0" + val;
        }
        result.push_back(val);
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"1", (std::string)"2", (std::string)"2", (std::string)"44", (std::string)"0", (std::string)"7", (std::string)"20257"}))) == (std::vector<std::string>({(std::string)"2", (std::string)"2", (std::string)"44", (std::string)"0", (std::string)"7", (std::string)"20257"})));
}
