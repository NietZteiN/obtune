#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string string, std::vector<long> numbers) {
    std::vector<std::string> arr;
    for (long num : numbers) {
        std::ostringstream ss;
        ss << std::setw(num) << std::setfill('0') << string;
        arr.push_back(ss.str());
    }
    std::string result;
    for(const auto &str : arr) {
        result += str + " ";
    }
    result.pop_back(); // remove the last space
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate(("4327"), (std::vector<long>({(long)2, (long)8, (long)9, (long)2, (long)7, (long)1}))) == ("4327 00004327 000004327 4327 0004327 4327"));
}
