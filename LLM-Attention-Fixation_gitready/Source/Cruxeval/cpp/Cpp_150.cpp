#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> numbers, long index) {
    for (long n : std::vector<long>(numbers.begin() + index, numbers.end())) {
        numbers.insert(numbers.begin() + index, n);
        index += 1;
    }
    return std::vector<long>(numbers.begin(), numbers.begin() + index);
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)-2, (long)4, (long)-4})), (0)) == (std::vector<long>({(long)-2, (long)4, (long)-4})));
}
