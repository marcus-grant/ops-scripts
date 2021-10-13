#!/usr/bin/env bats

_cmd="./pixel-ruler.sh"

@test "willful help prompt" {
  result="$(eval _cmd)"
  expected="
  [ "$result" -eq ]
}

