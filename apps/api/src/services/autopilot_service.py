from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import AutopilotRule, Recommendation
from src.repositories.autopilot_repository import AutopilotRepository
from src.schemas.autopilot import AutopilotRuleCreate, AutopilotRuleUpdate

class AutopilotService:
    def __init__(self,db:Session): self.db=db; self.repo=AutopilotRepository(db)
    def create(self,user_id:int,data:AutopilotRuleCreate)->AutopilotRule:
        return self.repo.create(AutopilotRule(user_id=user_id,**data.model_dump()))
    def get(self,user_id:int,item_id:int)->AutopilotRule:
        item=self.repo.get_for_user(item_id,user_id)
        if not item: raise HTTPException(status_code=404,detail="Правило автопилота не найдено")
        return item
    def list(self,user_id:int,limit:int,offset:int): return self.repo.list_for_user(user_id,limit,offset)
    def update(self,user_id:int,item_id:int,data:AutopilotRuleUpdate)->AutopilotRule:
        item=self.get(user_id,item_id)
        for k,v in data.model_dump(exclude_unset=True).items(): setattr(item,k,v)
        return self.repo.save(item)
    def delete(self,user_id:int,item_id:int)->None: self.repo.delete(self.get(user_id,item_id))
    def evaluate(self,user_id:int)->dict:
        rules=self.repo.enabled_for_user(user_id); products=self.repo.products_for_user(user_id)
        matched=created=0
        for rule in rules:
            for product in products:
                match=False; message=""; kind=f"autopilot.{rule.rule_type}"
                if rule.rule_type == "low_stock" and int(product.stock or 0) <= rule.threshold:
                    match=True; message=f"Остаток товара «{product.title}» снизился до {product.stock}."
                elif rule.rule_type == "low_seo" and float(product.seo_score or 0) < rule.threshold:
                    match=True; message=f"SEO-оценка товара «{product.title}» равна {product.seo_score:.1f}."
                elif rule.rule_type == "negative_profit" and float(product.profit_30d or 0) < rule.threshold:
                    match=True; message=f"Прибыль товара «{product.title}» за 30 дней: {product.profit_30d:.2f} ₽."
                if not match: continue
                matched+=1
                if self.repo.has_open_recommendation(user_id,product.id,kind): continue
                self.repo.add_recommendation(Recommendation(user_id=user_id,product_id=product.id,kind=kind,
                    title=rule.name,message=message,priority=rule.config.get("priority","high"),
                    action_data={"rule_id":rule.id,"threshold":rule.threshold}))
                created+=1
        return {"checked_products":len(products),"matched_rules":matched,"created_recommendations":created}
