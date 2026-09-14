#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::map<std::string,std::string> tags) {
    std::string resp = "";
    for (auto const& pair : tags) {
        resp += pair.first + " ";
    }
    return resp;
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,std::string>({{"3", "3"}, {"4", "5"}}))) == ("3 4 "));
}
