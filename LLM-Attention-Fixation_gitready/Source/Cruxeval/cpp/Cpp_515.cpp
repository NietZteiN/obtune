#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> result = array;
    std::reverse(result.begin(), result.end());
    for (long& item : result) {
        item *= 2;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>({(long)1, (long)2, (long)3, (long)4, (long)5}))) == (std::vector<long>({(long)10, (long)8, (long)6, (long)4, (long)2})));
}
