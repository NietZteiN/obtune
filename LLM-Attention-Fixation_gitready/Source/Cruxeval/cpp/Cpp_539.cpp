#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> array) {
    std::vector<std::string> array_copy = array;
    array_copy.push_back("");
    return array_copy;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>())) == (std::vector<std::string>({(std::string)""})));
}
