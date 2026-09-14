#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array, std::vector<long> lst) {
    array.insert(array.end(), lst.begin(), lst.end());
    
    std::vector<long> result;
    for (long e : array) {
        if (e % 2 == 0) {
            result.push_back(e);
        }
    }

    std::vector<long> finalResult;
    for (long e : array) {
        if (e >= 10) {
            finalResult.push_back(e);
        }
    }
    
    return finalResult;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)2, (long)15})), (std::vector<long>({(long)15, (long)1}))) == (std::vector<long>({(long)15, (long)15})));
}
