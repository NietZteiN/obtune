#include<assert.h>
#include<bits/stdc++.h>
typedef std::variant<std::string, long> Union_std_string_long;

std::vector<long> f(std::vector<Union_std_string_long> nums) {
    std::vector<long> digits;
    for (auto& num : nums) {
        if (std::holds_alternative<std::string>(num) && std::all_of(std::get<std::string>(num).begin(), std::get<std::string>(num).end(), ::isdigit)) {
            digits.push_back(std::stol(std::get<std::string>(num)));
        }
        else if (std::holds_alternative<long>(num)) {
            digits.push_back(std::get<long>(num));
        }
    }
    return digits;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<Union_std_string_long>({0, 6, "1", "2", 0}))) == (std::vector<long>({(long)0, (long)6, (long)1, (long)2, (long)0})));
}
