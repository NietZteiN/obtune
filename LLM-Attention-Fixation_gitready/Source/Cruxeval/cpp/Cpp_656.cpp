#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::vector<std::string> letters) {
    std::vector<std::string> a;
    for (int i = 0; i < letters.size(); i++) {
        if (std::find(a.begin(), a.end(), letters[i]) != a.end()) {
            return "no";
        }
        a.push_back(letters[i]);
    }
    return "yes";
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"b", (std::string)"i", (std::string)"r", (std::string)"o", (std::string)"s", (std::string)"j", (std::string)"v", (std::string)"p"}))) == ("yes"));
}
