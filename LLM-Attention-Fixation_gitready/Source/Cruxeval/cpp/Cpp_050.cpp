#include<assert.h>
#include<bits/stdc++.h>
std::vector<long> f(std::vector<std::string> lst) {
    lst.clear();
    std::vector<long> result(lst.size() + 1, 1);
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"a", (std::string)"c", (std::string)"v"}))) == (std::vector<long>({(long)1})));
}
