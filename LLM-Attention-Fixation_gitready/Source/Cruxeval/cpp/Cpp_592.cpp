#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> numbers) {
    std::vector<long> new_numbers;
    for(int i = 0; i < numbers.size(); i++) {
        new_numbers.push_back(numbers[numbers.size() - 1 - i]);
    }
    return new_numbers;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)11, (long)3}))) == (std::vector<long>({(long)3, (long)11})));
}
