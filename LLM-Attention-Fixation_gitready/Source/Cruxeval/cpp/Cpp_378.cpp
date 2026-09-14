#include<assert.h>
#include<bits/stdc++.h>
std::string f(std::map<std::string, long> dic, std::string key) {
    long v = (dic.find(key) != dic.end()) ? dic[key] : 0;
    if (v == 0)
        return "No such key!";
    dic.erase(key);
    return std::to_string(dic.begin()->second);
}
int main() {
    auto candidate = f;
    assert(candidate((std::map<std::string,long>({{"did", 0}})), ("u")) == "No such key!");
}
