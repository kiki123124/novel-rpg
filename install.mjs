#!/usr/bin/env node

import { execSync } from "child_process";
import { existsSync, mkdirSync } from "fs";
import { join } from "path";
import { homedir } from "os";

const SKILL_DIR = join(homedir(), ".openclaw", "skills", "novel-rpg");
const REPO_URL = "https://github.com/kiki123124/novel-rpg.git";

function run(cmd, opts = {}) {
  try {
    return execSync(cmd, { stdio: "inherit", ...opts });
  } catch {
    return null;
  }
}

function main() {
  const args = process.argv.slice(2);
  const cmd = args[0] || "install";

  if (cmd === "uninstall") {
    if (existsSync(SKILL_DIR)) {
      run(`rm -rf "${SKILL_DIR}"`);
      console.log("✓ novel-rpg skill 已卸载");
    } else {
      console.log("novel-rpg skill 未安装");
    }
    return;
  }

  if (cmd === "update") {
    if (existsSync(join(SKILL_DIR, ".git"))) {
      console.log("正在更新 novel-rpg skill...");
      run("git pull", { cwd: SKILL_DIR });
      run(`python3 "${join(SKILL_DIR, "scripts", "book_manager.py")}" init-builtins`);
      console.log("✓ 更新完成");
    } else {
      console.log("请先安装: npx novel-rpg-skill");
    }
    return;
  }

  // install
  console.log("正在安装 novel-rpg skill...\n");

  // 确保父目录存在
  const skillsDir = join(homedir(), ".openclaw", "skills");
  mkdirSync(skillsDir, { recursive: true });

  if (existsSync(SKILL_DIR)) {
    console.log("novel-rpg 已存在，正在更新...");
    run("git pull", { cwd: SKILL_DIR });
  } else {
    run(`git clone "${REPO_URL}" "${SKILL_DIR}"`);
  }

  // 初始化内置书籍
  run(`python3 "${join(SKILL_DIR, "scripts", "book_manager.py")}" init-builtins`);

  console.log("\n✓ novel-rpg skill 安装完成！");
  console.log("\n使用方式：");
  console.log("  对 AI 说「小说冒险」「开始冒险」「小说闯关」「novel rpg」");
  console.log("\n导入PDF小说：");
  console.log("  pip3 install PyMuPDF");
  console.log(`  python3 ${join(SKILL_DIR, "scripts", "pdf_import.py")} import "book.pdf" --book-id id --title "名"`);
}

main();
