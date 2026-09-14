#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<long> array) {
    std::vector<long> a;
    std::reverse(array.begin(), array.end());
    for (int i = 0; i < array.size(); i++) {
        if (array[i] != 0) {
            a.push_back(array[i]);
        }
    }
    std::reverse(a.begin(), a.end());
    return a;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<long>())) == (std::vector<long>()));
}
