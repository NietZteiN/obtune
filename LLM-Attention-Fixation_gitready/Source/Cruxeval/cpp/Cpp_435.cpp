#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> numbers, long num, long val) {
    while (numbers.size() < static_cast<size_t>(num)) {
        numbers.insert(numbers.begin() + numbers.size() / 2, std::to_string(val));
    }
    for (long i = 0; i < static_cast<long>(numbers.size() / (num - 1) - 4); ++i) {
        numbers.insert(numbers.begin() + numbers.size() / 2, std::to_string(val));
    }
    std::string result;
    for (const auto &number : numbers) {
        result += number + " ";
    }
    return result.substr(0, result.size() - 1);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>()), (0), (1)) == (""));
}
