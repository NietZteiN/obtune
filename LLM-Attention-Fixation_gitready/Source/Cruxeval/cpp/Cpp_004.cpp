#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> array) {
    std::string s = " ";
    for(const std::string& str: array) {
        s += str;
    }
    return s;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)" ", (std::string)"  ", (std::string)"    ", (std::string)"   "}))) == ("           "));
}
