#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> l, std::string c) {
    std::string result = "";
    for (const std::string& str : l) {
        result += str + c;
    }
    return result;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"many", (std::string)"letters", (std::string)"asvsz", (std::string)"hello", (std::string)"man"})), ("")) == ("manylettersasvszhelloman"));
}
