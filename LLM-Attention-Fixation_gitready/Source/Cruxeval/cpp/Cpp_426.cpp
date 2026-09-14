#include<assert.h>
#include<bits/stdc++.h>

std::vector<long> f(std::vector<long> numbers, long elem, long idx) {
    if(idx < numbers.size())
        numbers.insert(numbers.begin() + idx, elem);
    else
        numbers.push_back(elem);
    return numbers;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3})), (8), (5)) == (std::vector<long>({(long)1, (long)2, (long)3, (long)8})));
}
