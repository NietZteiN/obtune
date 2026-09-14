#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string s) {
    std::string nums;
    for(char c : s) {
        if(std::isdigit(c)) {
            nums.push_back(c);
        }
    }

    if(nums.empty()) {
        return "none";
    }

    std::istringstream iss(nums);
    std::vector<int> numbers;
    std::string num;
    while(std::getline(iss, num, ',')) {
        numbers.push_back(std::stoi(num));
    }

    int m = *std::max_element(numbers.begin(), numbers.end());
    return std::to_string(m);
}
int main() {
    auto candidate = f;
    assert(candidate(("01,001")) == ("1001"));
}
