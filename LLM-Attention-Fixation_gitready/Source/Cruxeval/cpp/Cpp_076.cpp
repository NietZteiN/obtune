#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> nums) {
    std::vector<long> result;
    for (auto y : nums) {
        if (y > 0) {
            result.push_back(y);
        }
    }
    
    if (result.size() <= 3) {
        return result;
    }
    
    std::reverse(result.begin(), result.end());
    size_t half = result.size() / 2;
    
    std::vector<long> finalResult;
    finalResult.insert(finalResult.end(), result.begin(), result.begin() + half);
    finalResult.insert(finalResult.end(), 5, 0);
    finalResult.insert(finalResult.end(), result.begin() + half, result.end());
    
    return finalResult;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)10, (long)3, (long)2, (long)2, (long)6, (long)0}))) == (std::vector<long>({(long)6, (long)2, (long)0, (long)0, (long)0, (long)0, (long)0, (long)2, (long)3, (long)10})));
}
