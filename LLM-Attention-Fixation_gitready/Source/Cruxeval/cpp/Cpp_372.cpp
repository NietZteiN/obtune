#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> list_, long num) {
    std::vector<std::string> temp;
    for (std::string i : list_) {
        long repeat = num / 2;
        std::string repeated_i = "";
        for (long j = 0; j < repeat; j++) {
            repeated_i += i + ",";
        }
        temp.push_back(repeated_i.substr(0, repeated_i.length() - 1));
    }
    return temp;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"v"})), (1)) == (std::vector<std::string>({(std::string)""})));
}
