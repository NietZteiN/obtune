#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string stg, std::vector<std::string> tabs) {
    for (std::string tab : tabs) {
        stg.erase(stg.find_last_not_of(tab) + 1);
    }
    return stg;
}
int main() {
    auto candidate = f;
    assert(candidate(("31849 let it!31849 pass!"), (std::vector<std::string>({(std::string)"3", (std::string)"1", (std::string)"8", (std::string)" ", (std::string)"1", (std::string)"9", (std::string)"2", (std::string)"d"}))) == ("31849 let it!31849 pass!"));
}
