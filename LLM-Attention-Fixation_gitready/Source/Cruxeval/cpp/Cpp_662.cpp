#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> values) {
    std::vector<std::string> names = {"Pete", "Linda", "Angela"};
    names.insert(names.end(), values.begin(), values.end());
    std::sort(names.begin(), names.end());
    return names;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"Dan", (std::string)"Joe", (std::string)"Dusty"}))) == (std::vector<std::string>({(std::string)"Angela", (std::string)"Dan", (std::string)"Dusty", (std::string)"Joe", (std::string)"Linda", (std::string)"Pete"})));
}
