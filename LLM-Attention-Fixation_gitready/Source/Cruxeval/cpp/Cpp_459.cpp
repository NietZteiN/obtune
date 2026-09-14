#include<assert.h>
#include<bits/stdc++.h>
std::map<std::string,std::string> f(std::vector<std::string> arr, std::map<std::string,std::string> d) {
    for (size_t i = 1; i < arr.size(); i += 2) {
        d[arr[i]] = arr[i-1];
    }
    return d;
}
int main() {
    auto candidate = f;
    assert(candidate((std::vector<std::string>({(std::string)"b", (std::string)"vzjmc", (std::string)"f", (std::string)"ae", (std::string)"0"})), (std::map<std::string,std::string>())) == (std::map<std::string,std::string>({{"vzjmc", "b"}, {"ae", "f"}})));
}
