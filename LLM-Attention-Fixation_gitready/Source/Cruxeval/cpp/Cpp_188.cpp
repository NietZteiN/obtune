#include<assert.h>
#include<bits/stdc++.h>
std::vector<std::string> f(std::vector<std::string> strings) {
    std::vector<std::string> new_strings;
    for (const std::string& string : strings) {
        std::string first_two = string.substr(0, 2);
        if (first_two[0] == 'a' || first_two[0] == 'p') {
            new_strings.push_back(first_two);
        }
    }

    return new_strings;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"a", (std::string)"b", (std::string)"car", (std::string)"d"}))) == (std::vector<std::string>({(std::string)"a"})));
}
