#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::string concat, std::map<std::string,std::string> di) {
    int count = di.size();
    for (int i = 0; i < count; i++) {
        if (di[std::to_string(i)].find(concat) != std::string::npos) {
            di.erase(std::to_string(i));
        }
    }
    return "Done!";
}
int main() {
    auto candidate = f;
    assert(candidate(("mid"), (std::map<std::string,std::string>({{"0", "q"}, {"1", "f"}, {"2", "w"}, {"3", "i"}}))) == ("Done!"));
}
